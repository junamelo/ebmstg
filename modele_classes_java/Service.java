package com.moov.facturation.catalogue;

import java.util.List;

/**
 * Service optionnel
 */
public class Service {
    
    // Attributs
    private String id;
    private String nom;
    private String code; // unique
    private TypeService typeService;
    
    // Relations
    private List<TarifService> tarifs;
    private List<Cycle> cycles;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    
    public TypeService getTypeService() { return typeService; }
    public void setTypeService(TypeService typeService) { this.typeService = typeService; }
    
    public List<TarifService> getTarifs() { return tarifs; }
    public void setTarifs(List<TarifService> tarifs) { this.tarifs = tarifs; }
    
    public List<Cycle> getCycles() { return cycles; }
    public void setCycles(List<Cycle> cycles) { this.cycles = cycles; }
}
