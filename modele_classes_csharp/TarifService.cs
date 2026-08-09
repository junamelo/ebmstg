namespace Moov.Facturation.Catalogue
{
    /// <summary>
    /// Tarification d'un service
    /// </summary>
    public class TarifService
    {
        // Attributs
        public string Id { get; set; }
        public string NomOption { get; set; }
        public double Prix { get; set; }
        
        // Relations
        public Service Service { get; set; }
    }
}
