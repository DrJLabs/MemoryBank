"use client";

import { useState } from "react";
import { Install } from "@/components/dashboard/Install";
import Stats from "@/components/dashboard/Stats";
import { SystemHealthCard } from "@/components/dashboard/SystemHealthCard";
import { DatabaseMetricsCard } from "@/components/dashboard/DatabaseMetricsCard";
import { AlertsCard } from "@/components/dashboard/AlertsCard";
import { BMADTrackingCard } from "@/components/dashboard/BMADTrackingCard";
import { WorkflowTracker } from "@/components/dashboard/WorkflowTracker";
import { StoryEpicTracker } from "@/components/dashboard/StoryEpicTracker";
import { AgentActivityTracker } from "@/components/dashboard/AgentActivityTracker";
import { TaskBurndownCard } from "@/components/dashboard/TaskBurndownCard";
import { ChecklistProgressCard } from "@/components/dashboard/ChecklistProgressCard";
import { MemoryFilters } from "@/app/memories/components/MemoryFilters";
import { MemoriesSection } from "@/app/memories/components/MemoriesSection";
import "@/styles/animation.css";

export default function DashboardPage() {
  const [bmadTrackersVisible, setBmadTrackersVisible] = useState(false);

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

          {/* Comprehensive BMAD Project Tracking Section */}
          <div className="space-y-4">
            <div className="flex justify-between items-center animate-fade-slide-down delay-6">
              <h2 className="text-xl font-semibold text-white">
                🎯 BMAD Project Tracking
              </h2>
              {!bmadTrackersVisible && (
                <button
                  onClick={() => setBmadTrackersVisible(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-300"
                >
                  Load BMAD Trackers
                </button>
              )}
            </div>
            
            {bmadTrackersVisible && (
              <>
                {/* BMAD Overview Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="animate-fade-slide-down delay-7">
                    <BMADTrackingCard />
                  </div>
                  <div className="animate-fade-slide-down delay-8">
                    <WorkflowTracker />
                  </div>
                  <div className="animate-fade-slide-down delay-9">
                    <AgentActivityTracker />
                  </div>
                </div>

                {/* Tasks & Checklists Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="animate-fade-slide-down delay-9.5">
                    <TaskBurndownCard />
                  </div>
                  <div className="animate-fade-slide-down delay-9.6">
                    <ChecklistProgressCard />
                  </div>
                </div>

                {/* Detailed Tracking Row */}
                <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
                  <div className="animate-fade-slide-down delay-10">
                    <StoryEpicTracker />
                  </div>
                </div>
              </>
            )}
          </div>

          <div>
            <div className="animate-fade-slide-down delay-11">
              <MemoryFilters />
            </div>
            <div className="animate-fade-slide-down delay-12">
              <MemoriesSection />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
