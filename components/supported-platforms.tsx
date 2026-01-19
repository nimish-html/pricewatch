"use client";

import { motion } from "framer-motion";

const platforms = [
    {
        name: "Amazon",
        icon: "/platforms/amazon.svg",
        status: "Supported",
        color: "text-orange-500",
    },
    {
        name: "Walmart",
        icon: "/platforms/walmart.svg",
        status: "Supported",
        color: "text-blue-600",
    },
    {
        name: "Target",
        icon: "/platforms/target.svg",
        status: "Coming Soon",
        color: "text-red-500",
    },
    {
        name: "eBay",
        icon: "/platforms/ebay.svg",
        status: "Coming Soon",
        color: "text-green-500",
    },
    {
        name: "Best Buy",
        icon: "/platforms/bestbuy.svg",
        status: "Coming Soon",
        color: "text-blue-500",
    },
];

export default function SupportedPlatforms() {
    return (
        <section className="py-16 px-4 md:px-8 bg-muted/30">
            <div className="max-w-(--breakpoint-xl) mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    viewport={{ once: true }}
                    className="text-center mb-10"
                >
                    <h2 className="text-2xl md:text-3xl font-medium tracking-tight mb-3">
                        Supported E-commerce Platforms
                    </h2>
                    <p className="text-muted-foreground text-sm max-w-lg mx-auto">
                        Track prices from major retailers. More platforms added weekly based on
                        community requests.
                    </p>
                </motion.div>

                <div className="flex flex-wrap justify-center gap-6 md:gap-8">
                    {platforms.map((platform, index) => (
                        <motion.div
                            key={platform.name}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3, delay: index * 0.05 }}
                            viewport={{ once: true }}
                            className="flex flex-col items-center gap-2"
                        >
                            <div
                                className={`w-20 h-20 rounded-2xl bg-card border border-border flex items-center justify-center ${platform.status !== "Supported" ? "opacity-50" : ""
                                    }`}
                            >
                                {/* Placeholder for platform icons */}
                                <span className={`text-2xl font-bold ${platform.color}`}>
                                    {platform.name.charAt(0)}
                                </span>
                            </div>
                            <span className="text-sm font-medium">{platform.name}</span>
                            <span
                                className={`text-xs px-2 py-0.5 rounded-full ${platform.status === "Supported"
                                    ? "bg-emerald-500/10 text-emerald-500"
                                    : "bg-muted text-muted-foreground"
                                    }`}
                            >
                                {platform.status}
                            </span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
