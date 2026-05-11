"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { setToken } from "@/lib/auth";
import { Footer } from "@/components/Footer";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const token = await api.login(email, password);
      setToken(token);
      router.push("/dashboard");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-surface-container-lowest min-h-screen flex flex-col">
      <main className="flex-grow flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-black text-primary tracking-tight mb-2">PropViz AI</h1>
            <p className="text-on-surface-variant text-sm">Real estate intelligence simplified.</p>
          </div>

          <div className="bg-surface-container-lowest rounded-xl p-8 shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant">
            <div className="mb-8">
              <h2 className="text-xl font-bold text-on-surface mb-1">Welcome back</h2>
              <p className="text-on-surface-variant text-sm">Please enter your details to sign in.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="block text-sm font-bold text-on-surface-variant" htmlFor="email">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full px-4 py-3 bg-white border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-outline"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-on-surface-variant" htmlFor="password">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-white border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-outline"
                />
              </div>

              {error && (
                <p className="text-sm text-error bg-error-container/30 border border-error/20 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary-container text-on-primary font-bold py-3.5 rounded-lg shadow-sm hover:opacity-95 transition-all active:scale-95 flex items-center justify-center gap-2 disabled:opacity-60"
              >
                <span>{loading ? "Signing in…" : "Login"}</span>
                {!loading && <span className="material-symbols-outlined text-[20px]">login</span>}
              </button>
            </form>
            <div className="mt-6 text-center">
              <p className="text-on-surface-variant text-sm">
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-primary font-bold hover:underline">
                  Create account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
