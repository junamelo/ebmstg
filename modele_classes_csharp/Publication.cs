using System;
using Moov.Facturation.Utilisateurs;

namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Publication de factures par un agent
    /// </summary>
    public class Publication
    {
        // Attributs
        public string Id { get; set; }
        public string CycleFacturation { get; set; }
        public DateTime PeriodeDebut { get; set; }
        public DateTime PeriodeFin { get; set; }
        public int NombreLignesTraitees { get; set; }
        public double MontantTotal { get; set; }
        
        // Relations
        public User Agent { get; set; }
    }
}
