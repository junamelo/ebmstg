using Moov.Facturation.Utilisateurs;

namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Historique des modifications de factures
    /// </summary>
    public class HistoriqueFacturation
    {
        // Attributs
        public string Id { get; set; }
        public TypeActionFacturation TypeAction { get; set; }
        public string AncienStatut { get; set; }
        public string NouveauStatut { get; set; }
        
        // Relations
        public Invoice Invoice { get; set; }
        public User User { get; set; }
    }
}
