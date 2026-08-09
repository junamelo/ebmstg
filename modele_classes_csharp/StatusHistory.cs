using System;

namespace Moov.Facturation.Utilisateurs
{
    /// <summary>
    /// Historique des changements de statut des utilisateurs
    /// </summary>
    public class StatusHistory
    {
        // Attributs
        public string Id { get; set; }
        public string OldStatus { get; set; }
        public string NewStatus { get; set; }
        public DateTime ChangedAt { get; set; }
        
        // Relations
        public User User { get; set; }
    }
}
