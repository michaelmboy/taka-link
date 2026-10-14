export type User = {id:number;name:string;email:string;role:"producer"|"collector"|"buyer"|"admin";phone?:string|null;organization?:string|null;service_area?:string|null};
export type Report = {id:number;title:string;description:string;waste_type:string;severity:string;status:string;latitude:number;longitude:number;image_url?:string|null;estimated_kg?:number|null;actual_kg?:number|null;created_at:string};
export type Listing = {id:number;title:string;material:string;description:string;price_per_kg:number;min_kg:number;location:string;buyer_id:number;buyer_name:string;active:boolean};
