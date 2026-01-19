"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { motion } from "framer-motion";

const faqItems = [
  {
    question: "How does PriceWatch track prices without getting blocked?",
    answer:
      "We use Thor Data's residential proxy network with 60+ million IPs worldwide. These are real residential IPs, not datacenter IPs, which makes our requests indistinguishable from normal users. Combined with intelligent fingerprinting and rate limiting, we achieve a 98%+ success rate.",
  },
  {
    question: "Which e-commerce platforms do you support?",
    answer:
      "Currently, we fully support Amazon (all regions) and Walmart. Target, eBay, Best Buy, and Shopify stores are coming soon. The open-source architecture makes it easy to add new platforms—contributions welcome!",
  },
  {
    question: "How often are prices updated?",
    answer:
      "You can configure scraping frequency from hourly to daily. More frequent scraping uses more proxy bandwidth, so we default to daily updates. For time-sensitive products, hourly monitoring is available.",
  },
  {
    question: "Is PriceWatch really free and open-source?",
    answer:
      "Yes! The entire codebase is MIT licensed on GitHub. You can self-host it with your own Thor Data credentials. We may offer a managed cloud version in the future for users who don't want to self-host.",
  },
  {
    question: "What data do you collect?",
    answer:
      "We only collect and store: product URLs you add, historical price data, and scraping logs. No personal data, no tracking, no ads. When self-hosting, all data stays on your own infrastructure.",
  },
  {
    question: "How do I get started with Thor Data proxies?",
    answer:
      "Sign up at thordata.com and get your API credentials. Thor Data offers a free trial so you can test PriceWatch before committing. Our setup docs walk you through the 5-minute configuration.",
  },
];

export default function Faq() {
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
            Frequently Asked Questions
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Everything you need to know about PriceWatch and price tracking.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto"
        >
          <Accordion type="single" collapsible className="w-full">
            {faqItems.map((item, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
}
