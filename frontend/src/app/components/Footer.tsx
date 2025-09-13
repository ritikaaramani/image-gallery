export default function Footer() {
  return (
    <footer style={{
      textAlign: "center",
      padding: "2rem 0",
      color: "#6b7280",
      fontSize: "0.9rem"
    }}>
      &copy; {new Date().getFullYear()} MyGallery. All rights reserved.
    </footer>
  );
}
