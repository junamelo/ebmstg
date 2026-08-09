namespace Moov.Facturation.Catalogue
{
    /// <summary>
    /// Enumération des types de forfaits
    /// </summary>
    public enum TypeForfait
    {
        /// <summary>
        /// Forfait data uniquement
        /// </summary>
        DATA,
        
        /// <summary>
        /// Forfait voix uniquement
        /// </summary>
        VOIX,
        
        /// <summary>
        /// Forfait SMS uniquement
        /// </summary>
        SMS,
        
        /// <summary>
        /// Forfait mixte (data + voix + SMS)
        /// </summary>
        MIXTE
    }
}
