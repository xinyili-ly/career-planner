import { VinylPlayer } from "@/components/vinyl-player"

export default function Page() {
  return (
    <main className="min-h-screen bg-[#E8F4F8] flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-black mb-2 text-black border-4 border-black bg-[#FFDE59] px-6 py-3 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] mb-10">
        Neo-Brutalism 唱片机
      </h1>
      <VinylPlayer />
      <p className="mt-8 text-lg font-bold text-black border-b-4 border-black">
        点击按钮或直接点击唱针来控制
      </p>
    </main>
  )
}
