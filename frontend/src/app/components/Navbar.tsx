"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
// app/components/Hero.tsx
import { Great_Vibes } from "next/font/google";

const greatVibes = Great_Vibes({
  weight: "400", // Great Vibes only has 400
  subsets: ["latin"],
});

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    router.push("/login");
  };

  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "1rem 2rem",
        background: "#ffece6ff",
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
        position: "sticky",
        top: 0,
        zIndex: 50,
        borderBottomLeftRadius: "12px",
        borderBottomRightRadius: "12px",
      }}
    >
      <section>
      <h1
        className={greatVibes.className}
        style={{
          fontSize: "2.3rem",
          marginBottom: "0.1rem",
          color: "#010008ff",
          textShadow: "0.5px 0.5px 0 #1f1074",
        }}
      >
        Lensify
      </h1>
      </section>
      <div style={{ display: "flex", gap: "1rem" }}>
        <button
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "10px",
            border: "none",
            background: "var(--accent)",
            color: "#ffffffff",
            fontWeight: 600,
            transition: "0.2s",
          }}
          onClick={() => router.push("/")}
        >
          Home
        </button>

        <button
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "10px",
            border: "1px solid rgba(15,23,42,0.1)",
            background: "transparent",
            color: "var(--text)",
            fontWeight: 500,
            transition: "0.2s",
          }}
          onClick={() => router.push("/about")}
        >
          About
        </button>

        {isLoggedIn ? (
          <button
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "10px",
              border: "none",
              background: "red",
              color: "#fff",
              fontWeight: 600,
              transition: "0.2s",
            }}
            onClick={handleLogout}
          >
            Logout
          </button>
        ) : (
          <>
            <button
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "10px",
                border: "none",
                background: "#a3b18a",
                color: "#fff",
                fontWeight: 600,
                transition: "0.2s",
              }}
              onClick={() => router.push("/login")}
            >
              Login
            </button>
            <button
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "10px",
                border: "none",
                background: "#e07a5f",
                color: "#fff",
                fontWeight: 600,
                transition: "0.2s",
              }}
              onClick={() => router.push("/register")}
            >
              Register
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
