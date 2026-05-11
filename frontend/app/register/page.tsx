"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { setToken } from "@/lib/auth";
import { Footer } from "@/components/Footer";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Register
      await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password, full_name: form.full_name }),
      }).then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail ?? "Registration failed");
        }
      });
      // Auto-login after register
      const token = await api.login(form.email, form.password);
      setToken(token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
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
            <p className="text-on-surface-variant text-sm">Create your account to get started.</p>
          </div>

          <div className="bg-surface-container-lowest rounded-xl p-8 shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant">
            <div className="mb-8">
              <h2 className="text-xl font-bold text-on-surface mb-1">Create account</h2>
              <p className="text-on-surface-variant text-sm">Start generating immersive property tours.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-sm font-bold text-on-surface-variant" htmlFor="full_name">
                  Full Name
                </label>
                <input
                  id="full_name"
                  type="text"
                  required
                  value={form.full_name}
                  onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
                  placeholder="Mohammad Mayaz"
                  className="w-full px-4 py-3 bg-white border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-outline"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-on-surface-variant" htmlFor="email">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
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
                  minLength={6}
                  value={form.password}
                  onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                  placeholder="Min. 6 characters"
                  className="w-full px-4 py-3 bg-white border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-outline"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-on-surface-variant" htmlFor="confirm">
                  Confirm Password
                </label>
                <input
                  id="confirm"
                  type="password"
                  required
                  value={form.confirm}
                  onChange={(e) => setForm((p) => ({ ...p, confirm: e.target.value }))}
                  placeholder="Repeat your password"
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
                className="w-full bg-primary-container text-on-primary font-bold py-3.5 rounded-lg shadow-sm hover:opacity-95 transition-all active:scale-95 disabled:opacity-60 flex items-center justify-center gap-2"
              >
                {loading ? "Creating account…" : "Create Account"}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-on-surface-variant text-sm">
                Already have an account?{" "}
                <Link href="/login" className="text-primary font-bold hover:underline">
                  Sign in
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
