using System;
using Moov.Facturation.Contrats;

namespace Moov.Facturation.Catalogue
{
    /// <summary>
    /// Cycle d'activation d'un service sur une ligne
    /// </summary>
    public class Cycle
    {
        // Attributs
        public string Id { get; set; }
        public DateTime DateDebut { get; set; }
        public DateTime DateFin { get; set; }
        
        // Relations
        public Line Line { get; set; }
        public Service Service { get; set; }
    }
}
