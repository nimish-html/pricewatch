import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import { Github, Twitter } from "lucide-react";

export default function Footer() {
  return (
    <footer className="py-12 px-4 md:px-8 bg-muted/30">
      <div className="max-w-(--breakpoint-xl) mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <h3 className="text-xl font-semibold mb-2">PriceWatch</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Open-source e-commerce price tracker.
              Track competitor prices with 98%+ success rate using residential proxies.
            </p>
            <div className="flex gap-4 mt-4">
              <Link
                href="https://github.com"
                target="_blank"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="w-5 h-5" />
              </Link>
              <Link
                href="https://twitter.com"
                target="_blank"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </Link>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-medium mb-3">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">

              <li>
                <Link href="#how-it-works" className="hover:text-foreground transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="#faq" className="hover:text-foreground transition-colors">
                  FAQ
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-medium mb-3">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link
                  href="https://github.com"
                  target="_blank"
                  className="hover:text-foreground transition-colors"
                >
                  GitHub
                </Link>
              </li>

              <li>
                <Link
                  href="/docs"
                  className="hover:text-foreground transition-colors"
                >
                  API Docs
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <Separator className="mb-6" />

        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} PriceWatch. MIT License.</p>

        </div>
      </div>
    </footer>
  );
}
