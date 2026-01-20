"use client";

import { motion } from "framer-motion";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Link2, Zap, LineChart, Bell } from "lucide-react";

const steps = [
    {
        icon: Link2,
        title: "Paste Product URL",
        description:
            "Add any Amazon or Walmart product link. We auto-detect the platform and start tracking.",
        color: "text-blue-500",
        bgColor: "bg-blue-500/10",
    },
    {
        icon: Zap,
        title: "We Scrape Securely",
        description:
            "High-quality residential proxies bypass anti-bot systems. 98% success rate, zero blocks.",
        color: "text-amber-500",
        bgColor: "bg-amber-500/10",
    },
    {
        icon: LineChart,
        title: "Track Price History",
        description:
            "View 30-day price charts, lowest/highest prices, and spot the best time to buy.",
        color: "text-emerald-500",
        bgColor: "bg-emerald-500/10",
    },
    {
        icon: Bell,
        title: "Get Price Alerts",
        description:
            "Set your target price and get notified instantly when prices drop below your threshold.",
        color: "text-purple-500",
        bgColor: "bg-purple-500/10",
    },
];

export default function HowItWorks() {
    return (
        <section className="py-20 px-4 md:px-8">
            <div className="max-w-(--breakpoint-xl) mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    viewport={{ once: true }}
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl md:text-4xl font-medium tracking-tight mb-4">
                        How It Works
                    </h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto">
                        Learn how to track competitor prices using production-grade scraping techniques.
                        Open source and easy to deploy.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <Card className="h-full relative overflow-hidden group hover:border-foreground/20 transition-colors">
                                <CardHeader>
                                    <div
                                        className={`w-12 h-12 rounded-xl ${step.bgColor} flex items-center justify-center mb-2`}
                                    >
                                        <step.icon className={`w-6 h-6 ${step.color}`} />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-medium text-muted-foreground">
                                            Step {index + 1}
                                        </span>
                                    </div>
                                    <CardTitle className="text-lg">{step.title}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <CardDescription className="text-sm">
                                        {step.description}
                                    </CardDescription>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
