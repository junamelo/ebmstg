package com.moovafrica.powerdesigner;

import jakarta.persistence.Entity;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "payeurs")
public class Payeur extends Utilisateur {

    @OneToMany(mappedBy = "payeur")
    private List<Contrat> contrats = new ArrayList<>(); // Payeur 1 -> 0..* Contrat
}
