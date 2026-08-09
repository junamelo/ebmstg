package com.moovafrica.powerdesigner;

import jakarta.persistence.Entity;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "agents_facturation")
public class AgentFacturation extends Utilisateur {

    @OneToMany(mappedBy = "agent")
    private List<HistoriqueFacturation> historiquesFacturation = new ArrayList<>(); // Agent 1 -> 0..* HistoriqueFacturation
}
