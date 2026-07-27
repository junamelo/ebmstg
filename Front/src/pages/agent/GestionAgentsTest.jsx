export default function GestionAgentsTest() {
  return (
    <div className="max-w-[1400px] mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-zinc-900 mb-4">
        Test - Gestion des Agents
      </h1>
      <p className="text-zinc-600 mb-8">
        Si vous voyez ce message, la route fonctionne ! ✅
      </p>
      
      <div className="bg-white border border-zinc-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Informations de débogage</h2>
        <ul className="space-y-2 text-sm">
          <li>✅ Route : /chef/agents</li>
          <li>✅ Composant : GestionAgentsTest.jsx</li>
          <li>✅ Import : Réussi</li>
          <li>✅ Rendu : Réussi</li>
        </ul>
        
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Prochaine étape :</strong> Remplacer ce composant test par le vrai GestionAgents.jsx
          </p>
        </div>
      </div>
    </div>
  )
}
