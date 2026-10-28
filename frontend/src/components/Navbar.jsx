import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      {/* Logo */}
      <Link to="/" className="navbar-logo">
        <img src="/againstericon.png" className="logo-icon" alt="againster logo" />
        <div className="logo">
          ag<span className="italic-words">ai</span>nster
        </div>
      </Link>

      {/* Navbar Links */}
      <div className="nav-links">
        <Link to="/" className="menu">Home</Link>
        <Link to="/help" className="menu">Help</Link>
      </div>
    </nav>
  );
}