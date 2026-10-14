"use client";
import {MapContainer, TileLayer, Marker, Popup, useMapEvents} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {useEffect} from "react";
import type {Report} from "@/lib/types";
const icon=L.icon({iconUrl:"https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",iconRetinaUrl:"https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",shadowUrl:"https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",iconSize:[25,41],iconAnchor:[12,41]});
function PinPicker({onPick}:{onPick?:(lat:number,lng:number)=>void}) { useMapEvents({click(e){onPick?.(e.latlng.lat,e.latlng.lng)}}); return null; }
export default function MapView({reports=[],onPick,center=[-0.1022,34.7617]}:{reports?:Report[];onPick?:(lat:number,lng:number)=>void;center?:[number,number]}) { useEffect(()=>{},[]); return <MapContainer center={center} zoom={11} scrollWheelZoom className="map-view"><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/><PinPicker onPick={onPick}/>{reports.map(r=><Marker key={r.id} position={[r.latitude,r.longitude]} icon={icon}><Popup><strong>{r.title}</strong><br/>{r.waste_type} · {r.status}<br/><a href={`https://www.openstreetmap.org/?mlat=${r.latitude}&mlon=${r.longitude}#map=16/${r.latitude}/${r.longitude}`} target="_blank" rel="noreferrer">Open map</a></Popup></Marker>)}</MapContainer> }
