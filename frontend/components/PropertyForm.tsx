"use client";
import { useState } from "react";
import { PropertyInput } from "@/lib/api";

interface Props {
  onSubmit: (data: PropertyInput) => void;
  loading?: boolean;
}

export function PropertyForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState<PropertyInput>({ name: "" });

  function set(key: keyof PropertyInput, value: string | number) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit(form); }}
      className="space-y-4"
    >
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Property Name <span className="text-red-500">*</span>
        </label>
        <input
          required
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          placeholder="e.g. ASSK Amari Maryland City"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Developer</label>
          <input
            value={form.developer ?? ""}
            onChange={(e) => set("developer", e.target.value)}
            placeholder="ASSK Amari Way Developers"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Unit Type</label>
          <input
            value={form.unit_type ?? ""}
            onChange={(e) => set("unit_type", e.target.value)}
            placeholder="e.g. Type A"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
        <input
          value={form.location ?? ""}
          onChange={(e) => set("location", e.target.value)}
          placeholder="F-Block, Sector 1, Aftabnagar, Dhaka"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Area (sqft)</label>
          <input
            type="number"
            value={form.area_sqft ?? ""}
            onChange={(e) => set("area_sqft", parseInt(e.target.value))}
            placeholder="1182"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Price Range</label>
          <input
            value={form.price_range ?? ""}
            onChange={(e) => set("price_range", e.target.value)}
            placeholder="e.g. 80–90 lakh BDT"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !form.name}
        className="w-full bg-brand-500 hover:bg-brand-600 disabled:bg-gray-300 text-white font-semibold py-2.5 rounded-lg transition-colors"
      >
        {loading ? "Creating…" : "Create Job"}
      </button>
    </form>
  );
}
