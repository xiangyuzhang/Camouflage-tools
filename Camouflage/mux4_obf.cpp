/**CFile****************************************************************
*
* FileName    [mux4_obf.cpp]
*
* Author      [Cunxi Yu]
*
* Date        [Ver. 1.0. Started - July 19, 2015.]
*
**Function*************************************************************
*
*   Synopsis    [New cam (mux4 based). Works for ISCAS 85/89 Verilog format]
*
************************************************************************
*/


#include <iostream>
#include <string>
#include <sstream>
#include <stdio.h>
#include <algorithm>
#include <fstream>
#include <unistd.h>
#include <functional>
#include <map>
#include <list>
#include <vector>
#include <cstdlib>
using namespace std;
void help()
{
    cout<<"mux4_obf [**-abcmap-fmt.v] [number(no. gate obf)]\n"
    "For example : mux4_obf c432-abcmap-fmt.v 1\n"
    "---> Randomly find ONE candidate to cam,  no using corruptibilty list\n";

}
struct seed_programbit
{
    int seed;
    int program_bit;
    vector<string> vec_str;
};
string int_string(int key)
{
    stringstream ss;
    ss<<key;
    string s;
    s = ss.str();
    return s;
}
bool If_Obf(string input)
{
    int count=0;
    string::iterator i;
    for (i=input.begin(); i!=input.end(); ++i) {
        if (*i == '.') {
            ++count;
        }
        else{ continue;}
    }
    if (count == 3) {
        return true;
    }
    else{
        return false;
    }
}
string Get_Input1(string input)
{
    int find_start = 0; find_start = input.find(".a(",0);
    int find_end =0;    find_end = input.find(")",find_start);
    string input1;
    input1.assign(input,find_start+3,find_end-find_start-3);
    return input1;
}
string Get_Input2(string input)
{
    int find_start = 0; find_start = input.find(".b(",0);
    int find_end =0;    find_end = input.find(")",find_start);
    string input2;
    input2.assign(input,find_start+3,find_end-find_start-3);
    return input2;
}
string Get_Output(string input)
{
    int find_start = 0; find_start = input.find(".O(",0);
    int find_end =0;    find_end = input.find(")",find_start);
    string input2;
    input2.assign(input,find_start+3,find_end-find_start-3);
    return input2;
}
string abcMap_MUX_OBF_netlist(string pi1,string pi2,string output, int seed,int programbit)
{
    string pi1_not = pi1+"_NOT";
    string pi2_not = pi2+"_NOT";
    string new_netlist;
    new_netlist+="inv1 gate( .a(" + pi1 + "),.O(" + pi1 + "_NOT) );\n";
    new_netlist+="inv1 gate( .a(" + pi2 + "),.O(" + pi2 + "_NOT));\n";
    new_netlist+="and2 gate( .a(" + pi1_not + "), .b(p" + int_string(programbit) + "), .O(EX" + int_string(seed+1) + ") );\n";
    ++seed;
    new_netlist+="and2 gate( .a(" + pi2_not + "), .b(EX" + int_string(seed) + "), .O(EX" + int_string(seed+1) + ") );\n"; ++seed;
    new_netlist+="and2 gate( .a(" + pi1 + "), .b(p" + int_string(programbit+1) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="and2 gate( .a(" + pi2_not + "), .b(EX" + int_string(seed) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="and2 gate( .a(" + pi1_not + "), .b(p" + int_string(programbit+2) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="and2 gate( .a(" + pi2 + "), .b(EX" + int_string(seed) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="and2 gate( .a(" + pi1 + "), .b(p" + int_string(programbit+3) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="and2 gate( .a(" + pi2 + "), .b(EX" + int_string(seed) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="or2  gate( .a(EX" + int_string(seed-6) + "), .b(EX" + int_string(seed-4) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="or2  gate( .a(EX" + int_string(seed-3) + "), .b(EX" + int_string(seed) + "), .O(EX" + int_string(seed+1) + ") );\n";++seed;
    new_netlist+="or2  gate( .a(EX" + int_string(seed-2) + "), .b(EX" + int_string(seed) + "), .O(" + output + ") );\n";
    return new_netlist;
}
void printserialSTR(int x)
{
    for (int i=1; i<=x; i++) {
        cout<<"EX"<<i<<",";
    }
}
string define_program_bits(int programbit)
{
    string return_str;
    return_str+="input ";
    int c_line=0;
    stringstream ss1;
    for (int i1=1; i1<=programbit; i1++) {
        ss1<<i1;
        return_str+="p"+ss1.str();
        ss1.str("");
        ++c_line;
        if(i1!=programbit)
        {
            return_str+=",";
            if (c_line ==10) {
                return_str+="\n        "; c_line=0;
            }
        }
        else{return_str+=";\n";}
    }
    return return_str;
}
string define_new_wire(int seed,vector<string> wire_vec_PI_NOT)
{
    string return_str;
    return_str+="     ";
    int c_line2=0;
    for (vector<string>::iterator i = wire_vec_PI_NOT.begin(); i!=wire_vec_PI_NOT.end(); ++i) {
        return_str+=*i+",";
        ++c_line2;
        if (c_line2==10) {
            return_str+="\n     ";c_line2=0;
        }
    }
    int changeline=0;
    stringstream ss1;
    for (int i2=1; i2<=seed; i2++) {
        ss1<<i2;
        return_str+="EX"+ss1.str();
        ss1.str("");
        ++changeline;
        if(i2!=seed)
        {
            return_str+=",";
            if (changeline==10) {
                return_str+="\n     "; changeline=0;
            }
        }
        else{return_str+=";\n";}
    }
    return return_str;
}
string mux4_obf_fileName(string file_in,int mux_num)
{
    int find_design=0; find_design = file_in.find("-",0);
    string fileout;
    fileout.assign(file_in,0,find_design);
    stringstream ss; ss<<mux_num;
    return fileout+"-mux4-"+ss.str()+".v";
}
int candidateNum(string file)
{
    ifstream fin(file.c_str());
    string input; int count =0;
    while(getline(fin,input))
    {
        if(If_Obf(input))
        {
            ++count;
        }
    }
    return count;
}
list<int> randomNum_Vec(int count, int HowMany)
{
    list<int> r;
    int randnum=0;
    while(r.size()<count && HowMany>=0)
    {
        randnum = rand() % count +1 ;
        r.push_back(randnum );
        r.sort(); r.unique();
        --HowMany;
    }
    return r;
}
bool random_Cam(list<int> randomNum, int num)
{
    list<int>::iterator i;
    bool b = false;
    for(i = randomNum.begin();i  != randomNum.end();i++)
    {
        if(*i == num)
        {
            b = true;
            break;
        }
    }
    return b;
}
void printListint(list<int> test)
{
    list<int>::iterator i;
    for(i=test.begin();i!=test.end();i++)
    {
        cout<<*i<<" "<<endl;
    }
}
seed_programbit s_p(string f,int mux_num,list<int> random_Cam_list)
{
    int seed=0;int programbit=1;
    vector<string> wire_vec_PI_NOT;
    ifstream fin(f.c_str()); //int num_muxObf=1;
    string input; int candidate_pos=0;
    while (getline(fin,input)) {
        if(If_Obf(input) && mux_num>=1)
        {
            ++candidate_pos;
            if(random_Cam( random_Cam_list, candidate_pos))   //candidate_pos is just the guess int,
            {
                string in1,in2,output;
                in1=Get_Input1(input); in2=Get_Input2(input); output = Get_Output(input);
                wire_vec_PI_NOT.push_back(in1+"_NOT");
                wire_vec_PI_NOT.push_back(in2+"_NOT");
                seed+=10;programbit+=4;
                --mux_num;
            }
        }
    }
    --programbit;
    seed_programbit *s_p, mem;
    s_p = & mem;
    s_p->seed = seed; s_p->program_bit=programbit;s_p->vec_str=wire_vec_PI_NOT;
    return *s_p;
}
int main(int argc, const char * argv[])
{
    help();
    seed_programbit *sp, mem;
    sp = &mem;
    string f = argv[argc-2];
    list<int> random_Cam_list;
    int num_muxObf=atoi(argv[argc-1]);
    random_Cam_list = randomNum_Vec(candidateNum(f), num_muxObf);
    *sp = s_p(f,num_muxObf,random_Cam_list);
    ofstream outfile(mux4_obf_fileName(f,num_muxObf).c_str());
    int seed=1;int programbit=1;
    //random cam
    int candidate_pos=0;
    vector<string> wire_vec_PI_NOT;
    ifstream fin(f.c_str());
    string input;
    int find_input=0; int find_end = 0; int find_wire=0; int find_comment=0;
    bool input_insert =false; bool wire_insert = false;
    while (getline(fin,input)) {
        find_input= input.find("input",0); find_end = input.find(";",0);
        find_wire = input.find("wire",0); find_comment = input.find("/",0);
        if(find_input==0){ input_insert = true;}
        if(find_wire ==0){ wire_insert = true;}
        if(find_comment==0)
        {
            continue;
        }
        if(If_Obf(input) && num_muxObf>=1  )
        {
            ++candidate_pos;
            if(random_Cam( random_Cam_list, candidate_pos))  //为什么总是33？先看懂random_Cam是什么
            {
                cout<<"the cam gate pos is : "<<candidate_pos<<endl;
                string in1,in2,output;
                in1=Get_Input1(input); in2=Get_Input2(input); output = Get_Output(input);
                wire_vec_PI_NOT.push_back(in1+"_NOT");
                wire_vec_PI_NOT.push_back(in2+"_NOT");
                outfile<<abcMap_MUX_OBF_netlist(in1, in2, output, seed, programbit);
                seed+=10;programbit+=4;
                --num_muxObf;
            }
            else
            {
                outfile<<input<<endl;
            }
        }
        else if(input_insert==true && find_end>=0)
        {
            int p = 0; p = sp->program_bit;
            //outfile<<p;
            outfile<<input<<endl;
            outfile<<"\n"<<define_program_bits(p);
            input_insert=false;
        }
        else if(wire_insert ==true && find_end>=0)
        {
            input.erase(find_end,1);input+=",";
            outfile<<input<<endl;
            outfile<<define_new_wire(sp->seed, sp->vec_str);
            wire_insert=false;
        }
        else
        {
            outfile<<input<<endl;
        }
}
--programbit;
}
