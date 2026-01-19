"use client";
/* eslint-disable @next/next/no-img-element */
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { motion } from "framer-motion";
import Link from "next/link";
import { TrendingDown, Bell, ShieldCheck, DollarSign } from "lucide-react";

export default function Hero() {
  return (
    <div className="relative justify-center items-center">
      <section className="max-w-(--breakpoint-xl) mx-auto px-4 py-28 gap-12 md:px-8 flex flex-col justify-center items-center">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{
            y: 0,
            opacity: 1,
          }}
          transition={{ duration: 0.6, type: "spring", bounce: 0 }}
          className="flex flex-col justify-center items-center space-y-5 max-w-4xl mx-auto text-center"
        >
          <span className="w-fit h-full text-sm bg-card px-3 py-1.5 border border-border rounded-full flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-emerald-500" />
            Open Source Price Intelligence
          </span>
          <h1 className="text-4xl font-medium tracking-tighter mx-auto md:text-6xl text-pretty bg-linear-to-b from-sky-800 dark:from-sky-100 to-foreground dark:to-foreground bg-clip-text text-transparent">
            Track Competitor Prices
            <br />
            Across the Web
          </h1>
          <p className="max-w-2xl text-lg mx-auto text-muted-foreground text-balance">
            Monitor Amazon, Walmart, and more with production-grade web scraping.
            Get price alerts, view trends, and never miss a deal again.
          </p>
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="items-center justify-center gap-x-4 flex flex-col sm:flex-row gap-y-3"
          >
            <Link href="/">
              <Button size="lg" className="shadow-lg">
                Start Tracking Prices
              </Button>
            </Link>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" size="lg">
                  Watch Demo
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle>PriceWatch Demo</DialogTitle>
                  <DialogDescription>
                    See how PriceWatch monitors competitor prices across e-commerce
                    platforms using Thor Data&apos;s residential proxies for 98%+
                    success rates.
                  </DialogDescription>
                </DialogHeader>
                <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                  <p className="text-muted-foreground">Demo video coming soon</p>
                </div>
                <DialogFooter>
                  <Button asChild size="sm">
                    <Link href="https://github.com" target="_blank">
                      View on GitHub
                    </Link>
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </motion.div>
        </motion.div>

        {/* Features highlight */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3, type: "spring", bounce: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12 w-full max-w-3xl"
        >
          <FeatureCard
            icon={<TrendingDown className="w-5 h-5 text-emerald-500" />}
            title="Price Tracking"
            description="30-day history"
          />
          <FeatureCard
            icon={<Bell className="w-5 h-5 text-amber-500" />}
            title="Price Alerts"
            description="Instant notifications"
          />
          <FeatureCard
            icon={<ShieldCheck className="w-5 h-5 text-blue-500" />}
            title="Anti-Detection"
            description="98%+ success rate"
          />
          <FeatureCard
            icon={<DollarSign className="w-5 h-5 text-purple-500" />}
            title="Multi-Platform"
            description="Amazon, Walmart +"
          />
        </motion.div>
      </section>

      {/* Background glow effect */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 2, delay: 0.5, type: "spring", bounce: 0 }}
        className="w-full h-full absolute -top-32 flex justify-end items-center pointer-events-none "
      >
        <div className="w-3/4 flex justify-center items-center">
          <div className="w-12 h-[600px] bg-emerald-500/20 blur-[100px] rounded-3xl max-sm:rotate-15 sm:rotate-35 will-change-transform"></div>
        </div>
      </motion.div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center p-4 bg-card/50 border border-border rounded-xl text-center">
      <div className="p-2 bg-background rounded-lg border border-border mb-2">
        {icon}
      </div>
      <h3 className="font-medium text-sm">{title}</h3>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
