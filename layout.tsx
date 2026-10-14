import type {Metadata} from "next";
import "./globals.css";
export const metadata:Metadata={title:"TakaLink | Waste to Value",description:"Report waste, coordinate collection and connect recoverable materials with buyers."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
