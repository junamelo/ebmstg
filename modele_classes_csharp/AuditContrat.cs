using System;
using Moov.Facturation.Utilisateurs;

namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Traçabilité des actions sur les contrats
    /// </summary>
    public class AuditContrat
    {
        // Attributs
        public string Id { get; set; }
        public TypeAction TypeAction { get; set; }
        public DateTime DateAction { get; set; }
        
        // Relations
        public Company Company { get; set; }
        public User User { get; set; }
    }
}
