package com.moov.facturation.catalogue;

import com.moov.facturation.contrats.Line;
import java.util.Date;

/**
 * Affectation d'un service à une ligne pendant une période
 */
public class Cycle {
    
    // Attributs
    private String id;
    private Date dateDebut;
    private Date dateFin;
    
    // Relations
    private Line line;
    private Service service;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public Date getDateDebut() { return dateDebut; }
    public void setDateDebut(Date dateDebut) { this.dateDebut = dateDebut; }
    
    public Date getDateFin() { return dateFin; }
    public void setDateFin(Date dateFin) { this.dateFin = dateFin; }
    
    public Line getLine() { return line; }
    public void setLine(Line line) { this.line = line; }
    
    public Service getService() { return service; }
    public void setService(Service service) { this.service = service; }
}
