package second_in_command.skills.tactical

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class FocusedFire : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("所有舰船的自动射击精度略有提高", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addSpacer(10f)
        tooltip.addPara("+10%% 非导弹武器射程", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+15%% 弹体飞行速率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-20%% 武器后坐力", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.recoilDecayMult.modifyMult(id, 1.2f)
        stats.recoilPerShotMult.modifyMult(id, 0.8f)
        stats.maxRecoilMult.modifyMult(id, 0.8f)

        stats.projectileSpeedMult.modifyPercent(id, 15f)

        stats.autofireAimAccuracy.modifyFlat(id, 0.2f)

        stats.ballisticWeaponRangeBonus.modifyPercent(id, 10f)
        stats.energyWeaponRangeBonus.modifyPercent(id, 10f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

}