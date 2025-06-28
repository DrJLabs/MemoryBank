"use client";

import { Install } from "@/components/dashboard/Install";
import Stats from "@/components/dashboard/Stats";
import { SystemHealthCard } from "@/components/dashboard/SystemHealthCard";
import { DatabaseMetricsCard } from "@/components/dashboard/DatabaseMetricsCard";
import { AlertsCard } from "@/components/dashboard/AlertsCard";
import { MemoryFilters } from "@/app/memories/components/MemoryFilters";
import { MemoriesSection } from "@/app/memories/components/MemoriesSection";
import "@/styles/animation.css";

export default function DashboardPage() {
  return (
    <div className="text-white py-6">
      <div className="container">
        <div className="w-full mx-auto space-y-6">
          <div className="grid grid-cols-3 gap-6">
            {/* Memory Category Breakdown */}
            <div className="col-span-2 animate-fade-slide-down">
              <Install />
            </div>

            {/* Memories Stats */}
            <div className="col-span-1 animate-fade-slide-down delay-1">
              <Stats />
            </div>
          </div>

          {/* Real-Time Monitoring Section */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white animate-fade-slide-down delay-2">
              🔍 System Monitoring
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="animate-fade-slide-down delay-3">
                <SystemHealthCard />
              </div>
              <div className="animate-fade-slide-down delay-4">
                <DatabaseMetricsCard />
              </div>
              <div className="animate-fade-slide-down delay-5">
                <AlertsCard />
              </div>
            </div>
          </div>

          <div>
            <div className="animate-fade-slide-down delay-6">
              <MemoryFilters />
            </div>
            <div className="animate-fade-slide-down delay-7">
              <MemoriesSection />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
