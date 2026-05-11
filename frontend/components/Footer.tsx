export function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest border-t border-outline-variant py-8 mt-auto">
      <div className="max-w-[1280px] mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex flex-col items-center md:items-start gap-1">
          <span className="text-lg font-bold text-primary">PropViz AI</span>
          <p className="text-xs text-on-surface-variant">© 2025 Win Win Properties. Powered by PropViz AI.</p>
        </div>
        <div className="flex gap-6 text-xs text-on-surface-variant">
          <a href="#" className="hover:text-primary transition-colors opacity-80 hover:opacity-100">Privacy Policy</a>
          <a href="#" className="hover:text-primary transition-colors opacity-80 hover:opacity-100">Terms of Service</a>
          <a href="#" className="hover:text-primary transition-colors opacity-80 hover:opacity-100">Contact Support</a>
        </div>
      </div>
    </footer>
  );
}
