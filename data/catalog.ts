export type Service={id:string;name:string;category:string;unit:'flat'|'sqft'|'each'|'room'|'bath';price:number;description:string;property:string[]}
export const propertyTypes=[
 {id:'single',name:'Casa unifamiliar',icon:'🏡',group:'Residencial'},{id:'townhouse',name:'Townhouse',icon:'🏘️',group:'Residencial'},{id:'apartment',name:'Apartamento / Condo',icon:'🏢',group:'Residencial'},
 {id:'office',name:'Oficina',icon:'🏬',group:'Comercial'},{id:'retail',name:'Tienda / Retail',icon:'🛍️',group:'Comercial'},{id:'restaurant',name:'Restaurante',icon:'🍽️',group:'Comercial'},{id:'bank',name:'Banco / Institución',icon:'🏦',group:'Comercial'},{id:'clinic',name:'Clínica / Médico',icon:'🏥',group:'Comercial'},{id:'warehouse',name:'Almacén / Warehouse',icon:'🏭',group:'Comercial'},{id:'other',name:'Otro',icon:'🏗️',group:'Otro'}]
export const services:Service[]=[
 {id:'bathroom',name:'Baños completos',category:'Áreas',unit:'bath',price:25,description:'Inodoro, lavamanos, espejo, superficies, piso y basura',property:['all']},
 {id:'kitchen',name:'Cocina',category:'Áreas',unit:'flat',price:35,description:'Counters, fregadero, superficies y exterior de electrodomésticos',property:['single','townhouse','apartment']},
 {id:'bedroom',name:'Dormitorios',category:'Áreas',unit:'room',price:15,description:'Polvo, superficies, cama exterior y piso',property:['single','townhouse','apartment']},
 {id:'living',name:'Sala / Living Room',category:'Áreas',unit:'flat',price:20,description:'Polvo, superficies y organización ligera',property:['single','townhouse','apartment']},
 {id:'dining',name:'Comedor',category:'Áreas',unit:'flat',price:15,description:'Mesa, superficies y piso',property:['single','townhouse','apartment','restaurant']},
 {id:'hall',name:'Pasillos y escaleras',category:'Áreas',unit:'flat',price:18,description:'Polvo, barandas y pisos',property:['all']},
 {id:'sweepmop',name:'Barrer y mapear pisos',category:'Pisos',unit:'sqft',price:.045,description:'Piso duro barrido y trapeado',property:['all']},
 {id:'vacuum',name:'Aspirar alfombra',category:'Pisos',unit:'sqft',price:.04,description:'Aspirado de áreas alfombradas',property:['all']},
 {id:'desks',name:'Escritorios / estaciones',category:'Comercial',unit:'each',price:4,description:'Superficie, polvo y desinfección ligera',property:['office','bank','clinic']},
 {id:'trash',name:'Vaciar botes de basura',category:'Comercial',unit:'each',price:2.5,description:'Retiro de bolsa y reemplazo',property:['office','retail','restaurant','bank','clinic','warehouse']},
 {id:'breakroom',name:'Break room',category:'Comercial',unit:'flat',price:25,description:'Counters, fregadero, mesas y piso',property:['office','bank','clinic','warehouse']},
 {id:'diningtables',name:'Mesas de restaurante',category:'Restaurante',unit:'each',price:3,description:'Limpiar y desinfectar mesa',property:['restaurant']},
 {id:'degrease',name:'Desengrase ligero cocina',category:'Restaurante',unit:'flat',price:55,description:'Superficies accesibles; no incluye hood exhaust',property:['restaurant']},
 {id:'examrooms',name:'Consultorios / exam rooms',category:'Clínica',unit:'each',price:12,description:'Superficies de alto contacto y piso; no incluye biohazard',property:['clinic']},
 {id:'interiorwindows',name:'Ventanas interiores',category:'Extras',unit:'flat',price:30,description:'Cristal interior accesible',property:['all']},
 {id:'fridge',name:'Interior refrigerador',category:'Extras',unit:'flat',price:45,description:'Limpieza interior del refrigerador vacío',property:['single','townhouse','apartment']},
 {id:'oven',name:'Interior horno',category:'Extras',unit:'flat',price:40,description:'Limpieza interior estándar',property:['single','townhouse','apartment']},
 {id:'cabinets',name:'Interior gabinetes',category:'Extras',unit:'flat',price:45,description:'Gabinetes vacíos',property:['single','townhouse','apartment']},
 {id:'baseboards',name:'Zócalos / Baseboards',category:'Extras',unit:'flat',price:40,description:'Limpieza detallada de zócalos',property:['all']},
 {id:'garage',name:'Garage - barrer',category:'Extras',unit:'flat',price:40,description:'Barrido de garage',property:['single','townhouse']},
 {id:'pet',name:'Cargo por mascotas',category:'Extras',unit:'flat',price:25,description:'Tiempo adicional por pelo de mascota',property:['single','townhouse','apartment']},
 {id:'carpetdeep',name:'Alfombra - limpieza profunda',category:'Especial',unit:'sqft',price:.25,description:'Estimado por pie²; sujeto a inspección',property:['all']}
]
export const frequency=[{id:'once',name:'Una sola vez',discount:0},{id:'weekly',name:'Semanal',discount:.15},{id:'twice',name:'Dos veces por semana',discount:.20},{id:'biweekly',name:'Quincenal',discount:.10},{id:'monthly',name:'Mensual',discount:.05}]
export const condition=[{id:'standard',name:'Estándar',multiplier:1},{id:'deep',name:'Profunda',multiplier:1.25},{id:'heavy',name:'Muy sucio',multiplier:1.5}]
