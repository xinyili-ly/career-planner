"use client"

import { useState } from "react"

export function VinylPlayer() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [needleOnRecord, setNeedleOnRecord] = useState(false)

  const togglePlay = () => {
    const newPlaying = !isPlaying
    setIsPlaying(newPlaying)
    // 如果停止播放，唱针也移开
    if (!newPlaying) {
      setNeedleOnRecord(false)
    }
  }

  const toggleNeedle = () => {
    const newNeedleState = !needleOnRecord
    setNeedleOnRecord(newNeedleState)
    // 唱针放下时自动播放，移开时自动停止
    setIsPlaying(newNeedleState)
  }

  return (
    <div className="flex flex-col items-center gap-8">
      {/* 唱片机主体 */}
      <div className="relative w-[400px] h-[400px] bg-[#FFDE59] border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-lg p-6">
        {/* 唱片底座 */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[280px] h-[280px] bg-[#FF6B6B] border-4 border-black rounded-full flex items-center justify-center">
          {/* 静态反光层 - 不随唱片旋转，播放时有闪烁效果 */}
          <div 
            className={`absolute w-[260px] h-[260px] rounded-full pointer-events-none z-20 ${isPlaying ? "animate-shimmer" : ""}`}
            style={{
              background: "linear-gradient(145deg, rgba(255,255,255,0.35) 0%, transparent 25%, transparent 75%, rgba(0,0,0,0.2) 100%)",
            }}
          />
          {/* 额外的弧形光斑 */}
          <div 
            className={`absolute w-[260px] h-[260px] rounded-full pointer-events-none z-20 ${isPlaying ? "animate-shimmer" : ""}`}
            style={{
              background: "radial-gradient(ellipse 40% 20% at 30% 25%, rgba(255,255,255,0.25) 0%, transparent 100%)",
              animationDelay: "0.5s",
            }}
          />
          {/* 唱片 */}
          <div
            className={`w-[260px] h-[260px] bg-[#1a1a1a] border-4 border-black rounded-full flex items-center justify-center relative overflow-hidden ${
              isPlaying ? "animate-spin-slow" : ""
            }`}
            style={{
              animationDuration: "3s",
            }}
          >
            {/* 唱片纹路 */}
            <div className="absolute inset-4 rounded-full border-2 border-gray-700" />
            <div className="absolute inset-8 rounded-full border-2 border-gray-700" />
            <div className="absolute inset-12 rounded-full border-2 border-gray-700" />
            <div className="absolute inset-16 rounded-full border-2 border-gray-700" />
            <div className="absolute inset-20 rounded-full border-2 border-gray-700" />
            
            {/* 反光效果 - 主光泽条 */}
            <div 
              className="absolute inset-0 rounded-full pointer-events-none"
              style={{
                background: "linear-gradient(135deg, transparent 30%, rgba(255,255,255,0.15) 45%, rgba(255,255,255,0.25) 50%, rgba(255,255,255,0.15) 55%, transparent 70%)",
              }}
            />
            
            {/* 反光效果 - 弧形高光 */}
            <div 
              className="absolute inset-0 rounded-full pointer-events-none"
              style={{
                background: "conic-gradient(from 0deg, transparent 0deg, rgba(255,255,255,0.1) 30deg, transparent 60deg, transparent 180deg, rgba(255,255,255,0.08) 210deg, transparent 240deg)",
              }}
            />
            
            {/* 唱片边缘高光 */}
            <div 
              className="absolute inset-0 rounded-full pointer-events-none border-4 border-transparent"
              style={{
                background: "linear-gradient(145deg, rgba(255,255,255,0.2) 0%, transparent 30%, transparent 70%, rgba(0,0,0,0.3) 100%)",
                WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                WebkitMaskComposite: "xor",
                maskComposite: "exclude",
                padding: "4px",
              }}
            />
            
            {/* 唱片标签 */}
            <div className="w-[80px] h-[80px] bg-[#FF9F43] border-4 border-black rounded-full flex items-center justify-center z-10 relative overflow-hidden">
              {/* 标签反光 */}
              <div 
                className="absolute inset-0 rounded-full pointer-events-none"
                style={{
                  background: "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, transparent 50%, rgba(0,0,0,0.1) 100%)",
                }}
              />
              <div className="w-[16px] h-[16px] bg-black rounded-full relative z-10" />
            </div>
          </div>
        </div>

        {/* 唱针臂 */}
        <div
          className={`absolute top-6 right-8 origin-top transition-transform duration-500 ease-in-out cursor-pointer ${
            needleOnRecord ? "rotate-[25deg]" : "rotate-[-15deg]"
          }`}
          onClick={toggleNeedle}
        >
          {/* 唱针底座 */}
          <div className="w-[30px] h-[30px] bg-[#C0C0C0] border-4 border-black rounded-full shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" />
          
          {/* 唱针臂 */}
          <div className="absolute top-[20px] left-1/2 -translate-x-1/2 w-[12px] h-[160px] bg-[#C0C0C0] border-4 border-black origin-top shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            {/* 唱针头 */}
            <div className="absolute bottom-[-30px] left-1/2 -translate-x-1/2">
              <div className="w-[24px] h-[40px] bg-[#2ECC71] border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]" />
              {/* 针尖 */}
              <div className="absolute bottom-[-10px] left-1/2 -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[12px] border-t-black" />
            </div>
          </div>
        </div>

        {/* 装饰螺丝 */}
        <div className="absolute top-3 left-3 w-4 h-4 bg-[#C0C0C0] border-2 border-black rounded-full" />
        <div className="absolute top-3 right-3 w-4 h-4 bg-[#C0C0C0] border-2 border-black rounded-full" />
        <div className="absolute bottom-3 left-3 w-4 h-4 bg-[#C0C0C0] border-2 border-black rounded-full" />
        <div className="absolute bottom-3 right-3 w-4 h-4 bg-[#C0C0C0] border-2 border-black rounded-full" />
      </div>

      {/* 控制按钮 */}
      <div className="flex gap-4">
        <button
          onClick={togglePlay}
          className={`px-6 py-3 font-bold text-lg border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none ${
            isPlaying ? "bg-[#FF6B6B] text-white" : "bg-[#2ECC71] text-black"
          }`}
        >
          {isPlaying ? "停止" : "播放"}
        </button>
        <button
          onClick={toggleNeedle}
          className={`px-6 py-3 font-bold text-lg border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none ${
            needleOnRecord ? "bg-[#FF9F43] text-black" : "bg-[#3498DB] text-white"
          }`}
        >
          {needleOnRecord ? "移开唱针" : "放下唱针"}
        </button>
      </div>

      {/* 状态指示 */}
      <div className="flex gap-6 text-lg font-bold">
        <div className="flex items-center gap-2">
          <div className={`w-4 h-4 border-2 border-black ${isPlaying ? "bg-[#2ECC71]" : "bg-gray-300"}`} />
          <span>唱片{isPlaying ? "转动中" : "停止"}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-4 h-4 border-2 border-black ${needleOnRecord ? "bg-[#FF9F43]" : "bg-gray-300"}`} />
          <span>唱针{needleOnRecord ? "在唱片上" : "移开"}</span>
        </div>
      </div>
    </div>
  )
}
