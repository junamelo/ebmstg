package com.moovafrica.powerdesigner;

import jakarta.persistence.Entity;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "employes")
public class Employe extends Utilisateur {

    @OneToMany(mappedBy = "employe")
    private List<Line> lignes = new ArrayList<>(); // Employe 1 -> 0..* Line
}
