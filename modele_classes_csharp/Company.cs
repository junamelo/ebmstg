using System.Collections.Generic;
using Moov.Facturation.Utilisateurs;
using Moov.Facturation.Facturation;

namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Contrat entreprise client
    /// </summary>
    public class Company
    {
        // Attributs
        public string Id { get; set; }
        public string Compte { get; set; } // unique
        public string RaisonSociale { get; set; }
        public CategorieClient Categorie { get; set; }
        public StatutFacturation StatutFactures { get; set; }
        public ModeReglement ModeReglement { get; set; }
        public bool EstResilie { get; set; }
        
        // Relations
        public Commercial Commercial { get; set; }
        public User Payeur { get; set; }
        public List<Line> Lines { get; set; }
        public List<Invoice> Invoices { get; set; }
        public List<AuditContrat> AuditContrats { get; set; }
        
        // Constructeur
        public Company()
        {
            Lines = new List<Line>();
            Invoices = new List<Invoice>();
            AuditContrats = new List<AuditContrat>();
        }
        
        // Méthodes métier
        /// <summary>
        /// Résilie le contrat
        /// </summary>
        public void Resilier()
        {
            EstResilie = true;
        }
    }
}
