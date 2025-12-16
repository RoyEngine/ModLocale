package second_in_command.skills.tactical

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class TacticalDrills : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("所有舰船的自动射击精度略微提高", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+5%% 所有舰船的武器伤害", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.ballisticWeaponDamageMult.modifyPercent(id, 5f)
        stats.energyWeaponDamageMult.modifyPercent(id, 5f)
        stats.missileWeaponDamageMult.modifyPercent(id, 5f)

        stats.autofireAimAccuracy.modifyFlat(id, 0.2f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

}