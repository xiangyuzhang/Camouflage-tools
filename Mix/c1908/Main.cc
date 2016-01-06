/*****************************************************************************************[Main.cc]
Copyright (c) 2003-2006, Niklas Een, Niklas Sorensson
Copyright (c) 2007,      Niklas Sorensson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
**************************************************************************************************/

#include <Python.h>
#include <sys/time.h>    
#include <errno.h>
#include <signal.h>
#include <zlib.h>
#include <sys/resource.h>
#include <iostream>
#include "utils/System.h"
#include "utils/ParseUtils.h"
#include "utils/Options.h"
#include "mod/Dimacs.h"
#include "simp/SimpSolver.h"

using namespace Minisat;

//=================================================================================================


void printStats(Solver& solver)
{
    double cpu_time = cpuTime();
    double mem_used = memUsedPeak();
    printf("restarts              : %"PRIu64"\n", solver.starts);
    printf("conflicts             : %-12"PRIu64"   (%.0f /sec)\n", solver.conflicts   , solver.conflicts   /cpu_time);
    printf("decisions             : %-12"PRIu64"   (%4.2f %% random) (%.0f /sec)\n", solver.decisions, (float)solver.rnd_decisions*100 / (float)solver.decisions, solver.decisions   /cpu_time);
    printf("propagations          : %-12"PRIu64"   (%.0f /sec)\n", solver.propagations, solver.propagations/cpu_time);
    printf("conflict literals     : %-12"PRIu64"   (%4.2f %% deleted)\n", solver.tot_literals, (solver.max_literals - solver.tot_literals)*100 / (double)solver.max_literals);
    if (mem_used != 0) printf("Memory used           : %.2f MB\n", mem_used);
    printf("CPU time              : %g s\n", cpu_time);
}


static Solver* solver;
// Terminate by notifying the solver and back out gracefully. This is mainly to have a test-case
// for this feature of the Solver as it may take longer than an immediate call to '_exit()'.
static void SIGINT_interrupt(int signum) { solver->interrupt(); }

// Note that '_exit()' rather than 'exit()' has to be used. The reason is that 'exit()' calls
// destructors and may cause deadlocks if a malloc/free function happens to be running (these
// functions are guarded by locks for multithreaded use).
static void SIGINT_exit(int signum) {
    printf("\n"); printf("*** INTERRUPTED ***\n");
    if (solver->verbosity > 0){
        printStats(*solver);
        printf("\n"); printf("*** INTERRUPTED ***\n"); }
    _exit(1); }


static void checkPyObj(PyObject * myPyObj, bool print=false) 
{
    /* print what is retrieved if 'print==true'  */
    PyObject *pyRepre;
    const char *strRepre; 
	if ( (!myPyObj) || (myPyObj==NULL) ){
		printf("Retrive python object failed >_< !\n");
		PyErr_Print();
		exit(1);
	} else if (print==true) {
		pyRepre = PyObject_Repr(myPyObj);
		strRepre = PyString_AsString(pyRepre);
		printf("\nRetrieve success: %s\n", strRepre);
	}
}


static PyObject* getPyClassInstance(char* inputfile, char* className) 
{
    PyObject *pyFileName, *pyModule, *pyDict, *pyClass, *pyInstance;
    // Build the name object:
    pyFileName = PyString_FromString(inputfile);
    // Load the module object:
    pyModule = PyImport_Import(pyFileName);
    checkPyObj(pyModule);
    Py_DECREF(pyFileName); 
    // build the dict for classes and functions in py file
    pyDict = PyModule_GetDict(pyModule);
    checkPyObj(pyDict);
    Py_DECREF(pyModule); 
    // get the name of a callable class from Python file: 
    pyClass = PyDict_GetItemString(pyDict,className);
    checkPyObj(pyClass);
    Py_DECREF(pyDict);
    // instantiation of the class:
    if (PyCallable_Check(pyClass)) pyInstance = PyObject_CallObject(pyClass, NULL); 
    Py_DECREF(pyClass);
    checkPyObj(pyInstance);
    return pyInstance;
}


//=================================================================================================
// Main:
static PyObject *pyInstance;
static PyObject *pyIniReTup, *pyReTup;
static PyObject *camPIndex, *camPOindex, *camCBindex, *camVarNum, *PItemp, *POtemp, *oracPONodes2grab, *oracPIls, *oracPOls, *camCNFile, *grabNodes, *addCons, *addonTup,  *cktTotVarNum, *newClausesNum, *miterOutIndex, *nodes2grab;
static Lit miterOut;

int main(int argc, char** argv)
{
    try {
        setUsageHelp("USAGE: %s [options] <input-file> <result-output-file>\n\n  where input may be either in plain or gzipped DIMACS.\n");
        // printf("This is MiniSat 2.0 beta\n");
        
#if defined(__linux__)
        fpu_control_t oldcw, newcw;
        _FPU_GETCW(oldcw); newcw = (oldcw & ~_FPU_EXTENDED) | _FPU_DOUBLE; _FPU_SETCW(newcw);
        printf("WARNING: for repeatability, setting FPU to use double precision\n");
#endif
        // Extra options:
        //
        IntOption    verb   ("MAIN", "verb",   "Verbosity level (0=silent, 1=some, 2=more).", 1, IntRange(0, 2));
        BoolOption   pre    ("MAIN", "pre",    "Completely turn on/off any preprocessing.", true);
        StringOption dimacs ("MAIN", "dimacs", "If given, stop after preprocessing and write the result to this file.");
        IntOption    cpu_lim("MAIN", "cpu-lim","Limit on CPU time allowed in seconds.\n", INT32_MAX, IntRange(0, INT32_MAX));
        IntOption    mem_lim("MAIN", "mem-lim","Limit on memory usage in megabytes.\n", INT32_MAX, IntRange(0, INT32_MAX));

        parseOptions(argc, argv, true);
        
        SimpSolver  S; // in simp folder
        double      initial_time = cpuTime(); //

        if (!pre) S.eliminate(true);

        S.verbosity = verb;
        
        solver = &S;
        // Use signal handlers that forcibly quit until the solver will be able to respond to
        // interrupts:
        signal(SIGINT, SIGINT_exit);
        signal(SIGXCPU,SIGINT_exit);

        // Set limit on CPU-time:
        if (cpu_lim != INT32_MAX){
            rlimit rl;
            getrlimit(RLIMIT_CPU, &rl);
            if (rl.rlim_max == RLIM_INFINITY || (rlim_t)cpu_lim < rl.rlim_max){
                rl.rlim_cur = cpu_lim;
                if (setrlimit(RLIMIT_CPU, &rl) == -1)
                    printf("WARNING! Could not set resource limit: CPU-time.\n");
            } }

        // Set limit on virtual memory:
        if (mem_lim != INT32_MAX){
            rlim_t new_mem_lim = (rlim_t)mem_lim * 1024*1024;
            rlimit rl;
            getrlimit(RLIMIT_AS, &rl);
            if (rl.rlim_max == RLIM_INFINITY || new_mem_lim < rl.rlim_max){
                rl.rlim_cur = new_mem_lim;
                if (setrlimit(RLIMIT_AS, &rl) == -1)
                    printf("WARNING! Could not set resource limit: Virtual memory.\n");
            } }
        /* 
        if (argc == 1)
            printf("Reading from standard input... Use '--help' for help.\n");

        gzFile in = (argc == 1) ? gzdopen(0, "rb") : gzopen(argv[1], "rb");
        if (in == NULL)
            printf("ERROR! Could not open file: %s\n", argc == 1 ? "<stdin>" : argv[1]), exit(1);
        
        if (S.verbosity > 0){
            printf("============================[ Problem Statistics ]=============================\n");
            printf("|                                                                             |\n"); }
        
        */
        
        // check argument number and initialization:
        if ( !fopen(argv[2], "r") ) {
            fprintf(stderr, "The oracle circuit file is suspicious.\n\n");
            return 0;            
        } else if (!fopen(argv[3], "r")) {
            fprintf(stderr, "The camoudlaged circuit file is suspicious.\n\n");
            return 0;
        }
       
        Py_Initialize();
        PySys_SetArgv(argc, argv);
        Py_SetProgramName(argv[0]); // optional 
        pyInstance = getPyClassInstance( argv[1], (char*)"DissectCkt" );
 
        /**********   Begin the decam algorithm    *************/       
        /**************** 1. find adequate PIPOs ****************/
        double sttTs;
        double endTs;
        FILE * iteTimeLog;
        iteTimeLog = fopen("increIterationInfo.log", "w");
        fprintf(iteTimeLog, "#iterationNumber\tvarNumber\tclauseNumber\titertionTime\n");
        lbool ret;    
        int cntnFlag = 1;
        int iteCnt = 1;
        int sizeOfNodes2grab=0;
        while (cntnFlag==1) { 
            sttTs = cpuTime();  
            if (iteCnt==1) { // Build the basic CNF file for the first iteration:
                char * methodName = (char * ) "initSolve"; 
                char * argFmt = (char *) "(sssi)";
                pyIniReTup = PyObject_CallMethod(pyInstance, methodName, argFmt, argv[2], argv[3], forbidOption, forbidBit);
                //check method is successfully called:
             	checkPyObj(pyIniReTup);
                // parse returned tup:
                camPIndex = PyTuple_GetItem(pyIniReTup, 0);
                camPOindex = PyTuple_GetItem(pyIniReTup, 1);  
                camCBindex = PyTuple_GetItem(pyIniReTup, 2);
                camVarNum = PyTuple_GetItem(pyIniReTup, 3);
                PItemp = PyTuple_GetItem(pyIniReTup, 4);
                POtemp = PyTuple_GetItem(pyIniReTup, 5);
                oracPONodes2grab = PyTuple_GetItem(pyIniReTup, 6);
                oracPIls = PyTuple_GetItem(pyIniReTup, 7);
                oracPOls = PyTuple_GetItem(pyIniReTup, 8);
                cktTotVarNum = PyTuple_GetItem(pyIniReTup, 9);
                camCNFile = PyTuple_GetItem(pyIniReTup, 10);
                miterOutIndex = PyTuple_GetItem(pyIniReTup, 11);
                nodes2grab = PyTuple_GetItem(pyIniReTup, 12);
                PyList_Append(nodes2grab, miterOutIndex);
                sizeOfNodes2grab = PyList_Size(nodes2grab);
                Py_DECREF(pyIniReTup);
            } else { // add CNF constraints for iterations after the initial one:  
                grabNodes = PyString_FromString("grabNodes"); // build py str obj
                if (!grabNodes) {
                	PyErr_Print();
                	exit(1);
                }
                pyReTup = PyObject_CallMethodObjArgs(pyInstance, grabNodes, camPIndex, camCBindex, camVarNum, oracPONodes2grab, oracPIls, oracPOls, NULL);
                if (!pyReTup) {
                	PyErr_Print();
                	exit(1);
                } else if (pyReTup==NULL) {
                    printf("Error in grabNodes method.\n");
                    break;
                } else {
                    // parse returned tup
                    cntnFlag = PyInt_AsLong((PyTuple_GetItem(pyReTup, 0)));
                    oracPIls = PyTuple_GetItem(pyReTup, 1);
                    oracPOls = PyTuple_GetItem(pyReTup, 2);
                    // check if the problem is resolved as SAT:
                    if (cntnFlag==0) {
                        Py_DECREF(pyReTup);
                        printf("Jumping out of loop .. ...\n");
                        break;
                    } else { 
                        printf("Current problem satisfied, continue solving...\n");
                        PItemp = PyTuple_GetItem(pyReTup, 3);
                        POtemp = PyTuple_GetItem(pyReTup, 4);
                        Py_DECREF(pyReTup);
                        addCons = PyString_FromString("addCons");
                        addonTup = PyObject_CallMethodObjArgs(pyInstance, addCons, cktTotVarNum, camVarNum, camCNFile, camCBindex, camPIndex, camPOindex, PItemp, POtemp, NULL);
                        cktTotVarNum=PyTuple_GetItem(addonTup, 0);
                        newClausesNum=PyTuple_GetItem(addonTup, 1);
                    }
                    Py_DECREF(grabNodes);
                	Py_DECREF(addCons);
                } 	             
            }

            // begin to solve one iteration within the loop:
			// "tmpIn.cnf" is the intermediate file generated by python
			static const char* infilename = "tmpIn.cnf";    
            if (iteCnt==1) printf("This is the first iteration\n");
            gzFile in = gzopen(infilename, "rb");
            if (in == NULL)
                //printf("ERROR! Could not open file: %s\n", argc == 1 ? "<stdin>" : argv[1]), exit(1); 
                printf("No file: %s.\n", infilename), exit(1);
                
            if (S.verbosity > 0){
                printf("============================[ Problem Statistics ]=============================\n");
                printf("|                                                                             |\n"); 
            }
            
            parse_DIMACS(in, S);
            gzclose(in); //close a compressed file stream, in std lib <zlib.h>;

            // fixed solution file: increIterationSolution.log
            FILE* res = fopen("increIterationSolution.log", "wb");


            if (S.verbosity > 0){
                printf("|  Number of variables:  %12d                                         |\n", S.nVars());
                printf("|  Number of clauses:    %12d                                         |\n", S.nClauses());
                fprintf(iteTimeLog, "%d\t%d\t", iteCnt, S.nVars());
                fprintf(iteTimeLog, "%d\t", S.nClauses());
            }
            double parsed_time = cpuTime();
            if (S.verbosity > 0){
                printf("|  Parse time:           %12.2f s                                       |\n", parsed_time - initial_time);
                printf("|                                                                             |\n"); 
            }
     
            // Change to signal-handlers that will only notify the solver and allow it to terminate
            // voluntarily:
            signal(SIGINT, SIGINT_interrupt);
            signal(SIGXCPU,SIGINT_interrupt);
            
            //checkPyObj(nodes2grab, true);
            for (int iteNodes2grab=0; iteNodes2grab<sizeOfNodes2grab;iteNodes2grab++) {
                PyObject *nodeIndex = PyList_GetItem(nodes2grab, iteNodes2grab);
                Py_INCREF(nodeIndex);
                int nodeIndexInt = (int) PyInt_AsLong(nodeIndex);
                S.setFrozen(nodeIndexInt-1, true);
                Py_DECREF(nodeIndex);
            }
            
            S.eliminate(true);
            double simplified_time = cpuTime();
            if (S.verbosity > 0){
                printf("|  Simplification time:  %12.2f s                                       |\n", simplified_time - parsed_time);
                printf("|                                                                             |\n"); 
            }
 
            if (!S.okay()){
                if (res != NULL) fprintf(res, "UNSAT\n"), fclose(res);
                if (S.verbosity > 0){
                    printf("===============================================================================\n");
                    printf("Solved by simplification\n");
                    printStats(S);
                    printf("\n"); }
                printf("UNSATISFIABLE\n");
                exit(20);
            }

            if (dimacs){
                if (S.verbosity > 0)
                    printf("==============================[ Writing DIMACS ]===============================\n");
                S.toDimacs((const char*)dimacs);
                if (S.verbosity > 0)
                    printStats(S);
                exit(0);
            }
           
            // use assumption here instead of a CNF clause in CNF file 
            int cMtrOutIndex = (int) PyInt_AsLong(miterOutIndex);
            /* set miter out to TRUE, notice, must use 'false' here */
            miterOut = mkLit(cMtrOutIndex-1, false);
            bool myRes = S.solve(miterOut);
            if (myRes==true) ret=l_True;
            else ret=l_False;

            if (S.verbosity > 0){
                printStats(S);
                printf("\n"); 
            }
            printf(ret == l_True ? "SATISFIABLE\n" : ret == l_False ? "UNSATISFIABLE\n" : "INDETERMINATE\n");
            if (res != NULL){
                if (ret == l_True){
                    fprintf(res, "SAT\n");
                    for (int i = 0; i < S.nVars(); i++)
                        if (S.model[i] != l_Undef)
                            fprintf(res, "%s%s%d", (i==0)?"":" ", (S.model[i]==l_True)?"":"-", i+1);
                    fprintf(res, " 0\n");
                } else if (ret == l_False)
                    fprintf(res, "UNSAT\n");
                else
                    fprintf(res, "INDET\n");
                fclose(res);
            }
            endTs = cpuTime();
            if (ret != l_False) {
                printf("%.4gs\n", endTs-sttTs);   
                fprintf(iteTimeLog, "%.4gs\n", endTs-sttTs);
                iteCnt += 1;
            } else {
                printf("%.4gs\n", endTs-sttTs);
                fprintf(iteTimeLog, "%.4gs\n", endTs-sttTs);
                fprintf(iteTimeLog, "This is the last UNSAT round.");
            }
            // freeze PI
            //PyObject *nodeIndex, *nodeValue;
            
            
            // freeze PO
            // freeze cb1
            // freeze cb2
            //sleep(5);
        }
        fclose(iteTimeLog);
        /* the finding PIPOs part is finished here !!! */

        
        /*************** 2. find final solution :  *************/
        PyObject * findSolu;
        findSolu = PyString_FromString("findSolu"); // build py str obj
        checkPyObj(findSolu);
        // call method grabNodes from instance pyInstance with PyObj args.
        PyObject * soluLine;
        PyObject * PyforbidOption = Py_BuildValue("s", forbidOption, sizeof(forbidOption));
        checkPyObj(PyforbidOption, true);
        PyObject * PyforbidBit = PyLong_FromLong( (long) forbidBit);
        checkPyObj(PyforbidBit, true);
        soluLine = PyObject_CallMethodObjArgs(pyInstance, findSolu, oracPIls, oracPOls, camVarNum, camCNFile, camCBindex, camPIndex, camPOindex, PyforbidOption, PyforbidBit, NULL);
        if (!soluLine) {
            PyErr_Print();
            exit(1);
        } else if (soluLine==NULL) {
            printf("Error in findSolu method.\n");
            exit(1);
        } 
        Py_DECREF(soluLine);        
        Py_DECREF(pyInstance);   
 
/*
        vec<Lit> dummy;
        lbool ret = S.solveLimited(dummy);
        if (S.verbosity > 0){
            printStats(S);
            printf("\n"); }
        printf(ret == l_True ? "SATISFIABLE\n" : ret == l_False ? "UNSATISFIABLE\n" : "INDETERMINATE\n");
        if (res != NULL){
            if (ret == l_True){
                fprintf(res, "SAT\n");
                for (int i = 0; i < S.nVars(); i++)
                    if (S.model[i] != l_Undef)
                        fprintf(res, "%s%s%d", (i==0)?"":" ", (S.model[i]==l_True)?"":"-", i+1);
                fprintf(res, " 0\n");
            }else if (ret == l_False)
                fprintf(res, "UNSAT\n");
            else
                fprintf(res, "INDET\n");
            fclose(res);
        }

#ifdef NDEBUG
        exit(ret == l_True ? 10 : ret == l_False ? 20 : 0);     // (faster than "return", which will invoke the destructor for 'Solver')
#else
        return (ret == l_True ? 10 : ret == l_False ? 20 : 0);
#endif
    */
    } catch (OutOfMemoryException&){
        printf("===============================================================================\n");
        printf("INDETERMINATE\n");
        exit(0);
    }
}
