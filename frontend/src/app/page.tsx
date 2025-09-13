// app/page.tsx (or HomePage.tsx if you named it that)
import Hero from "./components/Hero";
import Gallery from "./components/Gallery";

export default function HomePage() {
  return (
    <>
      {Hero && <Hero />}
      <Gallery />
    </>
  );
}
