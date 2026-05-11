"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/auth";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
  }

  const linkClass = (href: string) =>
    pathname === href
      ? "font-medium text-primary border-b-2 border-primary pb-1 transition-colors"
      : "font-medium text-on-surface-variant hover:bg-surface-container-low transition-colors px-2 py-1 rounded";

  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-surface border-b border-outline-variant shadow-sm h-16">
      <div className="max-w-[1280px] mx-auto px-8 h-full flex justify-between items-center">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-black text-primary tracking-tight">
            PropViz AI
          </Link>
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link href="/upload" className={linkClass("/upload")}>New Tour</Link>
            <Link href="/dashboard" className={linkClass("/dashboard")}>Dashboard</Link>
          </nav>
        </div>
        <button
          onClick={logout}
          className="material-symbols-outlined text-on-surface-variant hover:bg-surface-container-low p-2 rounded-full transition-colors"
        >
          logout
        </button>
      </div>
    </header>
  );
}
