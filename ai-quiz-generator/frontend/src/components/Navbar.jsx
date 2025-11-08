import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();
  const active = (p) => pathname.startsWith(p) ? "text-blue-600" : "text-gray-600";
  return (
    <nav className="flex items-center justify-between py-4">
      <div className="flex items-center gap-3">
        <img src="https://i.pravatar.cc/40" className="w-10 h-10 rounded-full" />
        <span className="font-semibold">Welcome, Candidate</span>
      </div>
      <div className="flex items-center gap-6">
        <Link className={`hover:text-blue-600 ${active("/")}`} to="/">Home</Link>
        <Link className={`hover:text-blue-600 ${active("/app")}`} to="/app">Dashboard</Link>
        <Link className="px-3 py-1 rounded-md bg-emerald-600 text-white" to="/exam">Take Quiz</Link>
      </div>
    </nav>
  );
}
