// app/components/Hero.tsx
import { Great_Vibes } from "next/font/google";

const greatVibes = Great_Vibes({
  weight: "400", // Great Vibes only has 400
  subsets: ["latin"],
});

export default function Hero() {
  return (
    <section
      style={{
        padding: "4rem 2rem",
        textAlign: "center",
        background: "linear-gradient(135deg, #e6beff 0%, #c2e9fb 100%)",
        borderRadius: "16px",
        marginBottom: "2rem",
      }}
    >
      <h1
        className={greatVibes.className}
        style={{
          fontSize: "4.7rem",
          marginBottom: "1rem",
          color: "#010008ff",
          textShadow: "0.5px 0.5px 0 #1f1074",
        }}
      >
        Welcome to Lensify
      </h1>

      <p style={{ color: "#1f1074ff", fontSize: "1.00rem", fontFamily: "Segoe UI", fontWeight: 500,}}>
        Capture the moment — your memories, your way.
      </p>
    </section>
  );
}
