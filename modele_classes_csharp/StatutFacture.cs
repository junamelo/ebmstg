namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Enumération des statuts de facture
    /// </summary>
    public enum StatutFacture
    {
        /// <summary>
        /// Facture brouillon (non finalisée)
        /// </summary>
        BROUILLON,
        
        /// <summary>
        /// Facture en cours de traitement
        /// </summary>
        EN_COURS,
        
        /// <summary>
        /// Facture validée
        /// </summary>
        VALIDEE,
        
        /// <summary>
        /// Facture publiée (visible client)
        /// </summary>
        PUBLIEE,
        
        /// <summary>
        /// Facture payée
        /// </summary>
        PAYEE,
        
        /// <summary>
        /// Facture annulée
        /// </summary>
        ANNULEE
    }
}
