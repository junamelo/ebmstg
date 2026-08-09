using System.Collections.Generic;
using Moov.Facturation.Utilisateurs;
using Moov.Facturation.Facturation;
using Moov.Facturation.Catalogue;

namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Ligne téléphonique d'un contrat
    /// </summary>
    public class Line
    {
        // Attributs
        public string Id { get; set; }
        public string Msisdn { get; set; } // unique (numéro 8 chiffres)
        public string Utilisateur { get; set; }
        public double Forfait { get; set; }
        public CycleFacturation Cycle { get; set; }
        public string Statut { get; set; }
        
        // Relations
        public Company Company { get; set; }
        public User Employe { get; set; }
        public List<Invoice> Invoices { get; set; }
        public List<Cycle> Cycles { get; set; }
        
        // Constructeur
        public Line()
        {
            Invoices = new List<Invoice>();
            Cycles = new List<Cycle>();
        }
    }
}
