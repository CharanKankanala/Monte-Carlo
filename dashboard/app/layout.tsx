import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multi-Asset Risk Lab",
  description: "Walk-forward portfolio research with GARCH, regimes, copulas, benchmarks and implementation costs.",
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
