using System;
using System.Collections.Generic;
using Moov.Facturation.Contrats;

namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Facture client (globale ou individuelle)
    /// </summary>
    public class Invoice
    {
        // Attributs
        public string Id { get; set; }
        public string NumeroFacture { get; set; } // unique
        public DateTime PeriodeDebut { get; set; }
        public DateTime PeriodeFin { get; set; }
        public double MontantTtc { get; set; }
        public StatutFacture Statut { get; set; }
        public string FichierPdf { get; set; }
        
        // Relations
        public Company Company { get; set; }
        public Line Line { get; set; } // nullable pour facture globale
        public List<NotificationFacture> Notifications { get; set; }
        public List<HistoriqueFacturation> Historique { get; set; }
        
        // Constructeur
        public Invoice()
        {
            Notifications = new List<NotificationFacture>();
            Historique = new List<HistoriqueFacturation>();
        }
        
        // Méthodes métier
        /// <summary>
        /// Publie la facture
        /// </summary>
        public void Publier()
        {
            Statut = StatutFacture.PUBLIEE;
        }
        
        /// <summary>
        /// Annule la facture
        /// </summary>
        public void Annuler()
        {
            Statut = StatutFacture.ANNULEE;
        }
    }
}
