(function(root){
  'use strict';
  function findRoute(routes,pu,drop){return routes.find(r=>r.pu===Number(pu)&&r.do===Number(drop))||null;}
  function readTrips(storage){try{const x=JSON.parse(storage.getItem('metroride-trips')||'[]');return Array.isArray(x)?x.filter(t=>typeof t.id==='string'&&typeof t.from==='string'&&typeof t.to==='string'&&Number.isFinite(t.fare)&&typeof t.date==='string'):[];}catch{return [];}}
  function saveTrip(storage,trips,route,from,to){if(!route||route.n<30)throw Error('Insufficient route evidence');const trip={id:globalThis.crypto?.randomUUID?.()||Date.now()+'-'+Math.random().toString(36).slice(2),from,to,fare:route.fare,date:new Date().toISOString(),status:'Simulated'};const next=[trip,...trips];storage.setItem('metroride-trips',JSON.stringify(next));return next;}
  const api={findRoute,readTrips,saveTrip};if(typeof module!=='undefined')module.exports=api;else root.MetroCore=api;
})(globalThis);
