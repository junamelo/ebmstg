using System.Collections.Generic;

namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Représente un commercial Moov Africa
    /// </summary>
    public class Commercial
    {
        // Attributs
        public string Id { get; set; }
        public string Nom { get; set; }
        public string Prenom { get; set; }
        public string Matricule { get; set; } // unique
        
        // Relations
        public List<Company> Companies { get; set; }
        
        // Constructeur
        public Commercial()
        {
            Companies = new List<Company>();
        }
    }
}
