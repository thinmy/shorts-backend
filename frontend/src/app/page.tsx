export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center">
          Bem-vindo à Shorts Platform
        </h1>
      </div>

      <div className="relative flex place-items-center before:absolute before:h-[300px] before:w-[480px] before:-translate-x-1/2 before:translate-y-1/2 before:rounded-full before:bg-gradient-radial before:from-white before:to-transparent before:blur-2xl before:content-[''] after:absolute after:-z-20 after:h-[180px] after:w-[240px] after:translate-x-1/3 after:bg-gradient-conic after:from-sky-200 after:via-blue-200 after:blur-2xl after:content-[''] before:dark:bg-gradient-to-br before:dark:from-transparent before:dark:to-blue-700 before:dark:opacity-10 after:dark:from-sky-900 after:dark:via-[#0141ff] after:dark:opacity-40 before:lg:h-[360px] z-[-1]">
        <div className="text-center">
          <h2 className="text-2xl mb-4">Crie, edite e compartilhe seus vídeos curtos</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Plataforma completa para criação de conteúdo de vídeo com IA integrada
          </p>
        </div>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-4 lg:text-left">
        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30">
          <h3 className="mb-3 text-2xl font-semibold">
            Upload de Vídeos
          </h3>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Faça upload dos seus vídeos e processe automaticamente com IA
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30">
          <h3 className="mb-3 text-2xl font-semibold">
            Download do YouTube
          </h3>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Baixe vídeos do YouTube para editar e repostar
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30">
          <h3 className="mb-3 text-2xl font-semibold">
            Transcrição com IA
          </h3>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Transcreva automaticamente usando OpenAI, Gemini ou Groq
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30">
          <h3 className="mb-3 text-2xl font-semibold">
            Compartilhamento Social
          </h3>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Publique diretamente no Instagram, TikTok, Twitter e YouTube
          </p>
        </div>
      </div>
    </main>
  )
}
