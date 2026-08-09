package com.moov.facturation.catalogue;

/**
 * Forfait tarifaire
 */
public class Package {
    
    // Attributs
    private String id;
    private String nom;
    private String code; // unique
    private TypeForfait typeForfait;
    private double prixMensuel;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    
    public TypeForfait getTypeForfait() { return typeForfait; }
    public void setTypeForfait(TypeForfait typeForfait) { this.typeForfait = typeForfait; }
    
    public double getPrixMensuel() { return prixMensuel; }
    public void setPrixMensuel(double prixMensuel) { this.prixMensuel = prixMensuel; }
}
