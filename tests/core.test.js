const test=require('node:test'),assert=require('node:assert/strict');
const {findRoute,readTrips,saveTrip}=require('../dist/core');
const route={pu:161,do:132,n:35,fare:88.5};
function storage(initial='[]'){let value=initial;return {getItem:()=>value,setItem:(k,v)=>{value=v;}};}
test('fare lookup is directed and missing routes stay missing',()=>{assert.equal(findRoute([route],161,132),route);assert.equal(findRoute([route],132,161),null);});
test('corrupt or invalid saved data does not break the app',()=>{for(const v of ['broken','null','{}','[{}]'])assert.deepEqual(readTrips(storage(v)),[]);});
test('supported trip can be saved, restored, and removed without a network',()=>{const s=storage();const list=saveTrip(s,[],route,'Midtown','JFK');assert.equal(list.length,1);assert.equal(readTrips(s)[0].fare,88.5);s.setItem('',JSON.stringify([]));assert.deepEqual(readTrips(s),[]);});
test('a route below the evidence threshold cannot be saved',()=>assert.throws(()=>saveTrip(storage(),[],{...route,n:29},'a','b')));
test('storage errors surface rather than reporting false success',()=>assert.throws(()=>saveTrip({setItem:()=>{throw Error('full');}},[],route,'a','b')));
