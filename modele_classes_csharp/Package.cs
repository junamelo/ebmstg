namespace Moov.Facturation.Catalogue
{
    /// <summary>
    /// Forfait tarifaire
    /// </summary>
    public class Package
    {
        // Attributs
        public string Id { get; set; }
        public string Nom { get; set; }
        public string Code { get; set; } // unique
        public TypeForfait TypeForfait { get; set; }
        public double PrixMensuel { get; set; }
    }
}
