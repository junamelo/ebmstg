using System.Collections.Generic;

namespace Moov.Facturation.Catalogue
{
    /// <summary>
    /// Service optionnel
    /// </summary>
    public class Service
    {
        // Attributs
        public string Id { get; set; }
        public string Nom { get; set; }
        public string Code { get; set; } // unique
        public TypeService TypeService { get; set; }
        
        // Relations
        public List<TarifService> Tarifs { get; set; }
        public List<Cycle> Cycles { get; set; }
        
        // Constructeur
        public Service()
        {
            Tarifs = new List<TarifService>();
            Cycles = new List<Cycle>();
        }
    }
}
