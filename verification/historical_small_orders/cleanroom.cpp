// Clean-room reference: definitions in paper/sections/02_prelim.tex only.
// Frozen before reading any project implementation. n <= 16.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
using Mask=uint32_t;
struct Graph {
 int n=0; array<Mask,16> a{};
 Mask all() const { return (Mask(1)<<n)-1; }
};
int count(Mask x){return __builtin_popcount(x);}
int low(Mask x){return __builtin_ctz(x);}
Graph decode(string s) {
 if(s.rfind(">>graph6<<",0)==0) s=s.substr(10);
 if(s.empty()) throw runtime_error("empty graph6");
 Graph g; g.n=int((unsigned char)s[0])-63;
 if(g.n<0 || g.n>16) throw runtime_error("order outside 0..16");
 int bits=g.n*(g.n-1)/2;
 if((int)s.size()<1+(bits+5)/6) throw runtime_error("truncated graph6");
 int p=0;
 for(int j=1;j<g.n;j++) for(int i=0;i<j;i++,p++) {
  int c=int((unsigned char)s[1+p/6])-63;
  if(c<0||c>63) throw runtime_error("bad graph6 byte");
  if((c>>(5-p%6))&1) {g.a[i]|=Mask(1)<<j; g.a[j]|=Mask(1)<<i;}
 }
 return g;
}
string encode(const Graph&g) {
 string s(1,char(g.n+63)); int x=0,k=0;
 for(int j=1;j<g.n;j++) for(int i=0;i<j;i++) {
  x=(x<<1)|int((g.a[i]>>j)&1); k++;
  if(k==6){s+=char(x+63);x=k=0;}
 }
 if(k) s+=char((x<<(6-k))+63);
 return s;
}
bool cone(const Graph&g,Mask s) {
 for(Mask v=s;v;v&=v-1) {int i=low(v);if((g.a[i]&s)==(s^(Mask(1)<<i)))return true;}
 return false;
}
bool connected(const Graph&g,Mask s) {
 if(!s)return false;
 Mask reached=s&-s,front=reached;
 while(front){Mask next=0;for(Mask b=front;b;b&=b-1)next|=g.a[low(b)];front=next&s&~reached;reached|=front;}
 return reached==s;
}
struct Faces { vector<vector<Mask>> f; long long chi=0; };
Faces faces(const Graph&g) {
 Faces c;c.f.resize(g.n+1);
 vector<unsigned char> ok(Mask(1)<<g.n);ok[0]=1;
 for(Mask s=1;s<=g.all();s++){
  int i=low(s);Mask t=s&(s-1);
  if(ok[t] && (t&g.a[i])==t) {
   ok[s]=1;int k=count(s);c.f[k].push_back(s);c.chi+=(k&1)?1:-1;
  }
 }
 return c;
}
int rank2(const vector<Mask>&rows,const vector<Mask>&cols,int n) {
 if(rows.empty()||cols.empty())return 0;
 vector<int> index(Mask(1)<<n,-1);
 for(size_t r=0;r<rows.size();r++)index[rows[r]]=int(r);
 const size_t words=(rows.size()+63)/64;
 vector<vector<uint64_t>> pivot(rows.size());
 int rank=0;
 for(Mask s:cols) {
  vector<uint64_t> col(words,0);
  for(Mask v=s;v;v&=v-1) {
   int r=index[s^(v&-v)];assert(r>=0);col[size_t(r)/64]^=uint64_t(1)<<(r%64);
  }
  for(;;) {
   int p=-1;
   for(int w=int(words)-1;w>=0;w--)if(col[w]) {p=w*64+63-__builtin_clzll(col[w]);break;}
   if(p<0)break;
   if(pivot[p].empty()){pivot[p]=move(col);rank++;break;}
   for(size_t w=0;w<words;w++)col[w]^=pivot[p][w];
  }
 }
 return rank;
}
vector<int> betti2(const Graph&g,const Faces&c) {
 vector<int> ranks(g.n+2,0), b;
 for(int k=2;k<=g.n;k++)ranks[k]=rank2(c.f[k-1],c.f[k],g.n);
 for(int k=1;k<=g.n;k++)b.push_back(int(c.f[k].size())-ranks[k]-ranks[k+1]-(k==1?1:0));
 return b;
}
bool acyclic2(const Graph&g,const Faces&c) {
 if(g.n==0)return false;
 auto b=betti2(g,c);
 return all_of(b.begin(),b.end(),[](int x){return x==0;});
}
struct VertexDeciders {
 const Graph&g;
 vector<int8_t> vm;
 array<vector<int8_t>,4> km;
 explicit VertexDeciders(const Graph&x):g(x),vm(Mask(1)<<x.n,-1) {
  for(auto&v:km)v.assign(Mask(1)<<x.n,-1);
 }
 bool ivs(Mask s) {
  if(!s)return false;if((s&(s-1))==0)return true;
  if(vm[s]>=0)return vm[s];
  if(!connected(g,s))return vm[s]=0;
  for(Mask b=s;b;b&=b-1){Mask v=b&-b;int i=low(v);
   if(ivs(g.a[i]&s)&&ivs(s^v))return vm[s]=1;
  }
  return vm[s]=0;
 }
 bool kd(Mask s,int k) {
  if(k==-1)return cone(g,s);
  if(!s)return false;if((s&(s-1))==0)return true;
  if(km[k][s]>=0)return km[k][s];
  if(!connected(g,s))return km[k][s]=0;
  for(Mask b=s;b;b&=b-1){Mask v=b&-b;int i=low(v);
   if(kd(g.a[i]&s,k-1)&&kd(s^v,k))return km[k][s]=1;
  }
  return km[k][s]=0;
 }
};
// Hashing locates buckets only; std::string equality compares every graph bit.
struct Strong {
 unordered_map<string,bool> memo;
 uint64_t queries=0, hits=0,states=0;
 string key(const Graph&g,Mask s) {
  vector<int> v;for(Mask b=s;b;b&=b-1)v.push_back(low(b));
  string z(1,char(v.size()));int x=0,k=0;
  for(size_t j=1;j<v.size();j++)for(size_t i=0;i<j;i++) {
   x=(x<<1)|int((g.a[v[i]]>>v[j])&1);k++;
   if(k==8){z+=char(x);x=k=0;}
  }
  if(k)z+=char(x<<(8-k));
  return z;
 }
 bool yes(Graph&g,Mask s) {
  queries++;
  if(!s)return false;if((s&(s-1))==0)return true;
  if(!connected(g,s))return false;
  if(cone(g,s))return true; // proved by recursive vertex deletion.
  string z=key(g,s);auto it=memo.find(z);
  if(it!=memo.end()){hits++;return it->second;}
  bool answer=false;
  for(Mask b=s;b&&!answer;b&=b-1) {
   Mask v=b&-b;int i=low(v);
   if(yes(g,g.a[i]&s)&&yes(g,s^v))answer=true;
  }
  for(int j=1;j<g.n&&!answer;j++)if((s>>j)&1)
   for(int i=0;i<j&&!answer;i++)if(((s>>i)&1)&&((g.a[i]>>j)&1)) {
    if(!yes(g,g.a[i]&g.a[j]&s))continue;
    g.a[i]^=Mask(1)<<j;g.a[j]^=Mask(1)<<i;
    answer=yes(g,s);
    g.a[i]^=Mask(1)<<j;g.a[j]^=Mask(1)<<i;
   }
  if(memo.size()>=2000000)memo.clear(); // eviction changes performance only.
  memo.emplace(move(z),answer);states++;
  return answer;
 }
 bool trace(Graph&g,Mask s,vector<string>&out) {
  if(count(s)==1)return true;
  for(Mask b=s;b;b&=b-1) {
   Mask v=b&-b;int i=low(v);Mask link=g.a[i]&s;
   if(yes(g,link)&&yes(g,s^v)){
    out.push_back("vertex "+to_string(i)+" link_mask="+to_string(link));
    return trace(g,s^v,out);
   }
  }
  for(int j=1;j<g.n;j++)if((s>>j)&1)for(int i=0;i<j;i++)
   if(((s>>i)&1)&&((g.a[i]>>j)&1)){
    Mask link=g.a[i]&g.a[j]&s;if(!yes(g,link))continue;
    g.a[i]^=Mask(1)<<j;g.a[j]^=Mask(1)<<i;
    if(yes(g,s)){
     out.push_back("edge "+to_string(i)+" "+to_string(j)+" link_mask="+to_string(link));
     return trace(g,s,out);
    }
    g.a[i]^=Mask(1)<<j;g.a[j]^=Mask(1)<<i;
   }
  return false;
 }
};
int main(int argc,char**argv) {
 string mode=argc>1?argv[1]:"classify";Strong st;string line;
 if(mode=="classify")cout<<"g6\tn\tchi\tz2\tIVS\tIS\tminus1\tk0\tk1\tk2\tk3\n";
 while(getline(cin,line)){
  if(line.empty()||line[0]=='#')continue;
  try{
   Graph g=decode(line);Mask s=g.all();
   if(mode=="roundtrip"){cout<<encode(g)<<"\n";continue;}
   if(mode=="strong"){cout<<line<<"\t"<<st.yes(g,s)<<"\n";continue;}
   if(mode=="trace"){
    cout<<"GRAPH "<<line<<" IS="<<st.yes(g,s)<<"\n";
    vector<string> out;if(st.yes(g,s)){bool ok=st.trace(g,s,out);assert(ok);for(auto&x:out)cout<<x<<"\n";}
    continue;
   }
   if(mode=="neighbors"){
    cout<<"GRAPH "<<line<<" IS="<<st.yes(g,s)<<"\n";
    for(int j=1;j<g.n;j++)for(int i=0;i<j;i++)if(!((g.a[i]>>j)&1)){
     Mask link=g.a[i]&g.a[j];
     if(st.yes(g,link)){
      g.a[i]|=Mask(1)<<j;g.a[j]|=Mask(1)<<i;
      cout<<i<<"\t"<<j<<"\t"<<encode(g)<<"\t"<<st.yes(g,s)<<"\n";
      g.a[i]^=Mask(1)<<j;g.a[j]^=Mask(1)<<i;
     }
    }
    cout<<"END\n";continue;
   }
   Faces c=faces(g);bool z2=acyclic2(g,c);
   if(mode=="homology2"){
    cout<<line<<"\tchi="<<c.chi<<"\tbetti_reduced=";auto b=betti2(g,c);
    for(size_t i=0;i<b.size();i++)cout<<(i?",":"")<<b[i];cout<<"\n";continue;
   }
   VertexDeciders vd(g);bool vs=vd.ivs(s);
   bool strong=vs||st.yes(g,s);
   cout<<line<<"\t"<<g.n<<"\t"<<c.chi<<"\t"<<z2<<"\t"<<vs<<"\t"<<strong<<"\t"<<cone(g,s);
   for(int k=0;k<=3;k++)cout<<"\t"<<vd.kd(s,k);cout<<"\n";
  }catch(const exception&e){cerr<<"ERROR "<<line<<": "<<e.what()<<"\n";return 2;}
 }
 cerr<<"exact_IS queries="<<st.queries<<" hits="<<st.hits<<" states="<<st.states<<" retained="<<st.memo.size()<<"\n";
}
